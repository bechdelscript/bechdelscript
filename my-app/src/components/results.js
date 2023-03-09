import { Component } from "react";
import CharacterList from "./characters_list";


class Results extends Component {

    render() {
        if (this.props.characters === null) {
            return;
        }
        return (
            <div>
                <div>{this.props.computed_score}</div>
                <div>
                    <CharacterList
                        characters={this.props.characters}
                        handleSubmit={this.props.handleSubmit}
                        handleChange={this.props.handleChange} />
                </div>
            </div>
        );
    }
}

export default Results;