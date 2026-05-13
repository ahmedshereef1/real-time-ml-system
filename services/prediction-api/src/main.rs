/* To run the server, use the command:
`cd prediction-api`
then: `cargo run`
This will create a folder called "target" in the prediction-api directory, which contains the compiled binary. You can run the server using the command:
`./target/debug/prediction-api`
The server will start and listen for incoming requests on the specified port. You can test the API endpoints using tools like curl or Postman.
*/

/* cargo install cargo-watch then  cargo watch -x run */
/* curl -sS http://127.0.0.1:3001/ */

use axum::{
    routing::get,
    extract::Query,
    Router,
};

use serde::Deserialize;
use sqlx::postgres::PgPoolOptions;

// This is how you denote the entrypoint of a Rust program that uses async with tokio
#[tokio::main]
async fn main() {

    // build our application with a route
    let app = Router::new()
        // `GET /health` goes to `health`
        .route("/health", get(health))
        .route("/prediction", get(get_prediction));
    // run our app with hyper, listening globally on port 3001
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001")
        .await
        .unwrap();

    axum::serve(listener, app)
        .await.unwrap();
}

// basic handler that responds with a static string
async fn health() -> &'static str {
    // let name: String = "my name".to_string();
    "I'm healthy!"
}

#[derive(Deserialize)]
struct PredictionParams {
    pair: String,
}

async fn get_prediction(params: Query<PredictionParams>) -> String {
    let pair: &String = &params.0.pair;

    // Return a message that depends on the pair
    // Create a connection pool so we can take to RisingWave (which under the hood os 
    // a postgres + other things)
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://root:123@localhost:4567/dev")
        .await.unwrap();
    
    // let row: (i64,) = sqlx::query_as("SELECT $1")
    //     .bind(150_i64)
    //     .fetch_one(&pool)
    //     .await
    //     .unwrap();
    // assert_eq!(row.0, 150);

    #[derive(sqlx::FromRow)]
    struct PredictionOutput { pair: String, predicted_price : f64 }

    let query = format!("SELECT pair , predicted_price FROM public.price_predictions WHERE pair = '{}'", pair);

    let prediction_output  = sqlx::query_as::<_, PredictionOutput>
        (&query)
        .fetch_one(&pool).await.unwrap();

    let output = format!("The price prediction for pair: {} is {}", prediction_output.pair, prediction_output.predicted_price);

    return output;
}