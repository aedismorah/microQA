import React, { useState } from 'react';
import axios from 'axios';

import './App.css'

var conf = require('./config.json');
const serverAddress = `http://${conf.ip}:${conf.port}`

function App() {
  const [similarAnswers, setSimilarAnswers] = useState(false);

  const get_questions = (e) => {
    if (e.key === 'Enter') {
      console.log(e.target.value)
      var query = `${serverAddress}/get_questions/`
      axios.post(query, {'query': e.target.value}).then((response) => {
        setSimilarAnswers(response.data['answers']);
        console.log(response.data['time'])
      });
    }
  }

  return (
    <div>
      <div id="registration_form">
        <input 
            type="text"
            placeholder="query"
            onKeyDown={(e) => get_questions(e)}
            id="prompt"
        />
        {similarAnswers && 
          <ul id="answers">
            {similarAnswers.map((answer, index) => 
              <li style={{padding: "4px", fontFamily: 'Helvetica', listStyle: 'none'}}>{answer}</li>
            )}
          </ul>
        }
      </div>
    </div>
  )
}

export default App;
