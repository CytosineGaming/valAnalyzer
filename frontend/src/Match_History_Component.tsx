import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

import "./match_history.css"

interface State {
  numClicks: number
  isFocused: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class Match_History_Component extends StreamlitComponentBase<State> {
  public state = { numClicks: 0, isFocused: false }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const agent = this.props.args["agent"]
    const place = this.props.args["place"]
    const kills = this.props.args["kills"]
    const deaths = this.props.args["deaths"]
    const assists = this.props.args["assists"]
    const ally_score = this.props.args["ally_score"]
    const enemy_score = this.props.args["enemy_score"]
    const result = this.props.args["result"]
    const start_time = this.props.args["start_time"]
    const game_map = this.props.args["map"]


    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    const style: React.CSSProperties = {}

    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {}
    
    // MAIN COMPONENT PROGRAM
    return (
      <div className="home-match-history-box">
        <div className="home-player-info-box">
          <img
            src={agent}
            alt="image"
            className="home-agent-icon"
          />
          <div className="home-kda-box">
            <span className="home-kda-title">K / D / A</span>
            <span className="home-kda-text">{kills} / {deaths} / {assists}</span>
          </div>
          <div className="home-place-box">
            <span className="home-place-text">{place}</span>
          </div>
        </div>
        <div className="home-score-box">
          <span className="home-score">
            <span className="home-text">{ally_score}</span>
            <span className="home-text1"> - </span>
            <span className="home-text2">{enemy_score}</span>
            <br></br>
          </span>
          <span className="home-result">
            <span>{result}</span>
            <br></br>
          </span>
        </div>
        <div className="home-match-info-box">
          <span className="home-game-time">{start_time}</span>
          <span className="home-map">
            <span>{game_map}</span>
            <br></br>
          </span>
        </div>
      </div>
    )
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(Match_History_Component)
