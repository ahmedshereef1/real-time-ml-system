/* To run the server, use the command:
`cd prediction-api`
then: `cargo run`
This will create a folder called "target" in the prediction-api directory, which contains the compiled binary. You can run the server using the command:
`./target/debug/prediction-api`
The server will start and listen for incoming requests on the specified port. You can test the API endpoints using tools like curl or Postman.
*/

/* cargo install cargo-watch then  cargo watch -x run */
/* curl -sS http://127.0.0.1:3009/ */

use axum::{
    routing::get, 
    Router,
};
use std::env;
mod routes;
mod db;
use routes::health::health;
use routes::prediction::get_prediction;

#[derive(Clone)]
struct AppState {
    pool: sqlx::PgPool,
}

// This is how you denote the entrypoint of a Rust program that uses async with tokio
#[tokio::main]
async fn main() {
    // Create a single PgPool at start up
    tracing_subscriber::fmt::init();
    let pool = db::get_pool().await;

    // Create the app state struct 
    let app_state = AppState { pool };

    // build our application with a route
    let app = Router::new()
        // `GET /health` goes to `health`
        .route("/health", get(health))
        .route("/prediction", get(get_prediction))
        .with_state(app_state);

    // run our app with hyper, listening globally on port 
    let port = env::var("PREDICTION_API_PORT").expect("PREDICTION_API_PORT must be set");
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", port))
        .await
        .expect("Failed to bind to port");

    tracing::info!("Listening on port {port}");

    axum::serve(listener, app)
        .await.unwrap();
}
