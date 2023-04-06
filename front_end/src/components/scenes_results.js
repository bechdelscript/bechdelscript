import { Component } from "react";
import SceneDisplayer from "./scene_displayer";

class ScenesResults extends Component {

    render() {
        let explanation;
        let scene_displayer = null;
        if (this.props.computed_score === 0) {
            explanation = "There is no two named female characters in this movie. See characters list below if you want to check by yourself."
        }
        else if (this.props.computed_score === 1) {
            explanation = "There are at least two named female characters in the movie. However, they don't seem to talk with each other throughout the film."
        }
        else if (this.props.computed_score === 2) {
            explanation = "Find below a few scenes where they talk :";
            scene_displayer = <SceneDisplayer scenes={this.props.scenes} user_key={this.props.user_key} />;
        }
        else if (this.props.computed_score === 3) {
            explanation = "There are at least two named female characters in the movie, they speak together, and not about men. Find below the scenes that pass the test :";
            scene_displayer = <SceneDisplayer scenes={this.props.scenes} user_key={this.props.user_key} />;
        }
        return (
            <div className="results-area-container">
                <div className="score-layout">
                    <h2>Score : {this.props.computed_score} / 3 </h2>
                </div>
                <h2>{this.props.message_result}</h2>
                <div>{explanation}</div>
                <br />
                <div className="center-text">{scene_displayer}</div>
            </div>);
    }
}

export default ScenesResults;
