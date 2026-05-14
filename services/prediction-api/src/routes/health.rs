// basic handler that responds with a static string
pub async fn health() -> &'static str {
    "I'm healthy!"
}