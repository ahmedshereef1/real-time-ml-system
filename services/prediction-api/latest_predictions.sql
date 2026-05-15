drop materialized view if exists :view_name;
set enable_locality_backfill = true;
create materialized view :view_name as
with latest_predictions as (
    select 
        pair,
        max(ts_ms) as last_ms
    from :table_name
    group by 1
)

SELECT
    p.pair,
    p.ts_ms,
    p.predicted_price,
    p.predicted_ts_ms
FROM 
    public.price_predictions p
    INNER JOIN latest_predictions lp 
        ON p.pair = lp.pair AND p.ts_ms = lp.last_ms
;