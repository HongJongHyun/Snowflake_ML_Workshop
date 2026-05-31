import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Snow편의점 매출 예측", page_icon="❄️", layout="wide")

session = get_active_session()

st.title("❄️ Snow편의점 매출 예측 대시보드")
st.caption("Snowflake ML Forecast 기반 30일 매출 예측 현황")

@st.cache_data(ttl=600)
def load_forecast():
    return session.sql("""
        SELECT FORECAST_DATE, REGION, CATEGORY_L1, PREDICTED_SALES, LOWER_BOUND, UPPER_BOUND, MODEL_VERSION
        FROM SNOW_ML_WORKSHOP.CVS_DEMO.SALES_FORECAST
        ORDER BY FORECAST_DATE
    """).to_pandas()

@st.cache_data(ttl=600)
def load_actual():
    return session.sql("""
        SELECT DS AS SALE_DATE, Y AS DAILY_SALES
        FROM SNOW_ML_WORKSHOP.CVS_DEMO.TS_DAILY_TOTAL
        ORDER BY DS DESC
        LIMIT 60
    """).to_pandas()

@st.cache_data(ttl=600)
def load_monitoring():
    return session.sql("""
        SELECT * FROM SNOW_ML_WORKSHOP.CVS_DEMO.ML_MONITORING_LOG
        ORDER BY EVAL_DATE DESC
        LIMIT 10
    """).to_pandas()

forecast_df = load_forecast()
actual_df = load_actual()
monitoring_df = load_monitoring()

total_forecast = forecast_df[forecast_df['CATEGORY_L1'] == '전체']
category_forecast = forecast_df[forecast_df['CATEGORY_L1'] != '전체']

with st.container(horizontal=True):
    st.metric(
        "30일 예측 총매출",
        f"₩{total_forecast['PREDICTED_SALES'].sum():,.0f}",
        border=True
    )
    st.metric(
        "예측 평균 일매출",
        f"₩{total_forecast['PREDICTED_SALES'].mean():,.0f}",
        border=True
    )
    st.metric(
        "최근 실제 평균 일매출",
        f"₩{actual_df['DAILY_SALES'].mean():,.0f}",
        border=True
    )
    if len(monitoring_df) > 0:
        latest_mape = monitoring_df.iloc[0].get('METRIC_VALUE', None)
        if latest_mape is not None and not pd.isna(latest_mape):
            st.metric(
                "모델 MAPE",
                f"{latest_mape:.1f}%",
                delta="정상" if latest_mape < 20 else "주의",
                delta_color="normal" if latest_mape < 20 else "inverse",
                border=True
            )
        else:
            st.metric("모델 MAPE", "—", delta="미측정", delta_color="off", border=True)
    else:
        st.metric("모델 MAPE", "—", delta="미측정", delta_color="off", border=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📈 실제 매출 vs 예측 매출")

        actual_chart = actual_df.copy()
        actual_chart['SALE_DATE'] = pd.to_datetime(actual_chart['SALE_DATE'])
        actual_chart = actual_chart.sort_values('SALE_DATE')
        actual_chart['TYPE'] = '실제 매출'
        actual_chart = actual_chart.rename(columns={'SALE_DATE': 'DATE', 'DAILY_SALES': 'SALES'})

        pred_chart = total_forecast[['FORECAST_DATE', 'PREDICTED_SALES']].copy()
        pred_chart['FORECAST_DATE'] = pd.to_datetime(pred_chart['FORECAST_DATE'])
        pred_chart['TYPE'] = '예측 매출'
        pred_chart = pred_chart.rename(columns={'FORECAST_DATE': 'DATE', 'PREDICTED_SALES': 'SALES'})

        combined = pd.concat([actual_chart[['DATE', 'SALES', 'TYPE']], pred_chart[['DATE', 'SALES', 'TYPE']]])

        chart = alt.Chart(combined).mark_line(strokeWidth=2).encode(
            x=alt.X('DATE:T', title='날짜'),
            y=alt.Y('SALES:Q', title='매출액 (원)'),
            color=alt.Color('TYPE:N', legend=alt.Legend(title="구분"),
                           scale=alt.Scale(domain=['실제 매출', '예측 매출'], range=['#2196F3', '#F44336'])),
            strokeDash=alt.StrokeDash('TYPE:N', scale=alt.Scale(domain=['실제 매출', '예측 매출'], range=[[0], [5,5]]))
        ).properties(height=350)

        band = alt.Chart(total_forecast).mark_area(opacity=0.15, color='#F44336').encode(
            x=alt.X('FORECAST_DATE:T'),
            y='LOWER_BOUND:Q',
            y2='UPPER_BOUND:Q'
        )

        st.altair_chart(band + chart, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("📊 카테고리별 30일 예측 매출")

        cat_totals = category_forecast.groupby('CATEGORY_L1')['PREDICTED_SALES'].sum().reset_index()
        cat_totals = cat_totals.sort_values('PREDICTED_SALES', ascending=False)

        bar_chart = alt.Chart(cat_totals).mark_bar(color='#2196F3', cornerRadiusTopRight=4, cornerRadiusTopLeft=4).encode(
            x=alt.X('CATEGORY_L1:N', sort='-y', title='카테고리'),
            y=alt.Y('PREDICTED_SALES:Q', title='예측 매출 합계 (원)'),
            tooltip=['CATEGORY_L1', alt.Tooltip('PREDICTED_SALES:Q', format=',.0f')]
        ).properties(height=350)

        st.altair_chart(bar_chart, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("🏆 카테고리별 예측 추이 (Top 5)")

        top5 = cat_totals.head(5)['CATEGORY_L1'].tolist()
        top5_data = category_forecast[category_forecast['CATEGORY_L1'].isin(top5)].copy()
        top5_data['FORECAST_DATE'] = pd.to_datetime(top5_data['FORECAST_DATE'])

        line_chart = alt.Chart(top5_data).mark_line(strokeWidth=2).encode(
            x=alt.X('FORECAST_DATE:T', title='날짜'),
            y=alt.Y('PREDICTED_SALES:Q', title='예측 매출 (원)'),
            color=alt.Color('CATEGORY_L1:N', title='카테고리'),
            tooltip=['FORECAST_DATE:T', 'CATEGORY_L1:N', alt.Tooltip('PREDICTED_SALES:Q', format=',.0f')]
        ).properties(height=300)

        st.altair_chart(line_chart, use_container_width=True)

with col4:
    with st.container(border=True):
        st.subheader("🔍 모델 모니터링 이력")

        if len(monitoring_df) > 0:
            display_cols = ['MODEL_NAME', 'MODEL_VERSION', 'EVAL_DATE', 'METRIC_NAME', 'METRIC_VALUE', 'IS_ALERT', 'NOTES']
            available_cols = [c for c in display_cols if c in monitoring_df.columns]
            st.dataframe(monitoring_df[available_cols], hide_index=True, use_container_width=True)
        else:
            st.info("아직 모니터링 기록이 없습니다. 노트북을 먼저 실행하세요.")

with st.container(border=True):
    st.subheader("📋 예측 상세 데이터")
    category_filter = st.selectbox("카테고리 필터", ['전체'] + sorted(category_forecast['CATEGORY_L1'].unique().tolist()))

    if category_filter == '전체':
        display_df = total_forecast
    else:
        display_df = category_forecast[category_forecast['CATEGORY_L1'] == category_filter]

    st.dataframe(
        display_df[['FORECAST_DATE', 'CATEGORY_L1', 'PREDICTED_SALES', 'LOWER_BOUND', 'UPPER_BOUND']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "FORECAST_DATE": st.column_config.DateColumn("예측 날짜"),
            "CATEGORY_L1": "카테고리",
            "PREDICTED_SALES": st.column_config.NumberColumn("예측 매출"),
            "LOWER_BOUND": st.column_config.NumberColumn("하한"),
            "UPPER_BOUND": st.column_config.NumberColumn("상한"),
        }
    )
