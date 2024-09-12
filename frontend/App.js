import { useState } from 'react'

function Page() {
  const [goals, setGoals] = useState('')  // Track user goals input
  const [useGpt2, setUseGpt2] = useState(false)  // Track GPT-2 usage
  const [depthLevel, setDepthLevel] = useState('general')  // Track depth level
  const [recommendations, setRecommendations] = useState([])  // Store recommendations
  const [gpt2Response, setGpt2Response] = useState(null)  // Store GPT-2 response
  const [questionsToAsk, setQuestionsToAsk] = useState([])  // Track dynamically generated questions

  const handleChange = (event) => {
    setGoals(event.target.value)
  }

  const handleDepthLevelChange = (event) => {
    setDepthLevel(event.target.value)
  }

  const handleGpt2Change = (event) => {
    setUseGpt2(event.target.checked)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    try {
      const response = await fetch('https://rele3ivh.clj5khk.gcp.restack.it/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          goals: goals.split(',').map(goal => goal.trim()),  // Split and trim goals
          api_key: process.env.REACT_APP_OPENAI_API_KEY,  // OpenAI API Key from env variable
          use_gpt2: useGpt2,  // Whether to use GPT-2
          depth_level: depthLevel  // Depth level (general, specific, precise)
        })
      })
      const data = await response.json()
      setRecommendations(data.recommendations)
      setGpt2Response(data.gpt2_response)
      setQuestionsToAsk(data.questions_to_ask)  // Update questions dynamically
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    }
  }

  return (
    <div>
      <h1>Supplement Recommendation</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Enter your health goals (comma separated):
          <input
            type="text"
            value={goals}
            onChange={handleChange}
          />
        </label>
        <br/>
        <label>
          Select Depth Level:
          <select value={depthLevel} onChange={handleDepthLevelChange}>
            <option value="general">General</option>
            <option value="specific">Specific</option>
            <option value="precise">Precise</option>
          </select>
        </label>
        <br/>
        <label>
          Use GPT-2 for more complex recommendations?
          <input
            type="checkbox"
            checked={useGpt2}
            onChange={handleGpt2Change}
          />
        </label>
        <br/>
        <button type="submit">Get Recommendations</button>
      </form>

      <h2>Recommendations</h2>
      <ul>
        {recommendations.map((recommendation, index) => (
          <li key={index}>{recommendation}</li>
        ))}
      </ul>

      {gpt2Response && (
        <div>
          <h2>GPT-2 Supplement Advice</h2>
          <p>{gpt2Response}</p>
        </div>
      )}

      <h2>Dynamic Questions</h2>
      <ul>
        {questionsToAsk.map((question, index) => (
          <li key={index}>{question}</li>
        ))}
      </ul>
    </div>
  )
}

export default Page

