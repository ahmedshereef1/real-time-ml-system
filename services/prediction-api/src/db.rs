use sqlx::postgres::PgPoolOptions;
use sqlx::PgPool;
use std::env;

pub async fn get_pool() -> PgPool {
    
    let database_url = env::var("PREDICTION_API_DATABASE_URL").unwrap();

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await.unwrap();
    
    return pool
}