// Defining a data model.
class SentimentScore {
  coin string
  // coin "BTC" | "ETH" # Feel free to use an enum instead to make this more robust
  score "1" | "-1"
}

class SentimentScores {
  scores SentimentScore[]
  reason string @description("The reason for the sentiment scores")
}

// Create a function to extract the resume from a string.
function ExtractSentimentScores(news: string) -> SentimentScores {
  client CustomSonnet4 // Make sure to set the ANTHROPIC_API_KEY as environment variable
  prompt #"
    You are an expert crypto financial analyst with deep knowledge of market dynamics
    and sentiment analysis. Analyze the following news story and determine its potential
    impact on crypto asset prices.

    Focus on both direct mentions and indirect implications for each asset.

    Do not output data for a given coin if the news is not relevant to it.
    {{ news }}

    {{ ctx.output_format }}
  "#
}


// Test the function with a sample resume. Open the VSCode playground to run this.
test goldman_sachs_news {
  functions [ExtractSentimentScores]
  args {
    news #"
      Goldman Sachs is about to buy 1B in Bitcoin, and sell 1B in Ethereum.
    "#
  }

  @@assert( {{ this.scores == [{"coin": "BTC", "score": "1"}, {"coin": "ETH", "score": "-1"}] }})

}
