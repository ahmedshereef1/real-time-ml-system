/* To run the server, use the command:
`cd prediction-api`
then: `cargo run`
This will create a folder called "target" in the prediction-api directory, which contains the compiled binary. You can run the server using the command:
`./target/debug/prediction-api`
The server will start and listen for incoming requests on the specified port. You can test the API endpoints using tools like curl or Postman.
*/

/* cargo install cargo-watch then  cargo watch -x run */
/* curl -sS http://127.0.0.1:3009/ */

mod routes;
mod db;
mod config;

use axum::{
    routing::get, 
    Router,
};
use sqlx::PgPool;
use log::info;

use routes::health::health;
use routes::prediction::get_prediction;
use config::Config;

#[derive(Clone)]
struct AppState {
    pool: PgPool,
    config: Config,
}

// This is how you denote the entrypoint of a Rust program that uses async with tokio
#[tokio::main]
async fn main() {
    
    // Start the logger as early as possible as you can
    env_logger::init();
    info!("starting up");

    // Load environment into a config struct
    let config: Config = Config::from_env(); 

    // Creating a single PgPool at start up
    info!("Creating pg pool...");
    let pool = db::get_pool(
        &config.pg_host,
        &config.pg_port,
        &config.pg_database,
        &config.pg_user,
        &config.pg_password,
    ).await;
    info!("Created pg pool!");

    // Create the app state struct 
    let app_state = AppState { pool, config: config.clone() };

    // build our application with a route
    let app = Router::new()
        // `GET /health` goes to `health`
        .route("/health", get(health))
        .route("/prediction", get(get_prediction))
        .with_state(app_state);

    // run our app with hyper, listening globally on port 
    // let port = env::var("PREDICTION_API_PORT").expect("PREDICTION_API_PORT must be set");
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", &config.api_port)).await.unwrap();
    axum::serve(listener, app)
        .await.unwrap();
}
