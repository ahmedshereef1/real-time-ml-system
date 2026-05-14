use axum::{
    extract::Query,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::postgres::PgPoolOptions;


#[derive(Deserialize)]
pub struct PredictionParams {
    pair: String,
}

#[derive(Serialize, sqlx::FromRow)]
pub struct PredictionOutput {
    pair: String,
    predicted_price: f64,
}

pub async fn get_prediction(params: Query<PredictionParams>) -> Json<PredictionOutput> {
    let pair: &String = &params.0.pair;

    // Create a connection pool so we can take to RisingWave (which under the hood os 
    // a postgres + other things)
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:123@localhost:4567/dev")
        .await.unwrap();

    let query = format!("SELECT pair , predicted_price FROM public.price_predictions WHERE pair = '{}'", pair);

    // If we want to return the prediction for a specific pair, we can do:
    let prediction_output  = sqlx::query_as::<_, PredictionOutput>
        (&query)
        .fetch_one(&pool).await.unwrap();
        
    let output = Json(PredictionOutput {
        pair: prediction_output.pair,
        predicted_price: prediction_output.predicted_price,
    });

    // If we want to return all the predictions for all pairs, we can do:
    // let prediction_output  = sqlx::query_as::<_, PredictionOutput>
    //     (&query)
    //     .fetch_all(&pool).await.unwrap();
    // let output = prediction_output.iter()
    //     .map(|p| format!("The price prediction for pair: {} is {}", p.pair, p.predicted_price))
    //     .collect::<Vec<_>>()
    //     .join("\n");

    return output;
}