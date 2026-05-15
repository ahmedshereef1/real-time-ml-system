use axum::{
    extract:: {Query, State},
    Json,
};
use serde::{Deserialize, Serialize};
use log::info;

use crate::AppState;

#[derive(Deserialize)]
pub struct PredictionParams {
    pair: String,
}

#[derive(Serialize, sqlx::FromRow)]
pub struct PredictionOutput {
    pair: String,
    predicted_price: f64,
}

pub async fn get_prediction(
    params: Query<PredictionParams>,
    State(app_state): State<AppState>,
) -> Json<PredictionOutput> {

    let pair: &String = &params.0.pair;
    info!("Requested prediction");

    let pool = &app_state.pool;
    let pg_view = app_state.config.pg_view_name;

    // let query = format!("SELECT pair , predicted_price FROM public.price_predictions WHERE pair = '{}'", pair);
    let query = format!("SELECT pair, predicted_price FROM public.{} WHERE pair = '{}'", pg_view, pair);

    // If we want to return the prediction for a specific pair, we can do:
    let prediction_output  = sqlx::query_as::<_, PredictionOutput>
        (&query)
        .fetch_one(pool).await.unwrap();
        
    let output = Json(PredictionOutput {
        pair: prediction_output.pair,
        predicted_price: prediction_output.predicted_price,
    });

    info!("Returning prediction to the client");

    return output;
}