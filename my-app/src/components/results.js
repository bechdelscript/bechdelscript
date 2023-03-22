import React, { Component } from "react";
import CharacterList from "./characters_list";
import ScenesResults from "./scenes_results";



class Results extends Component {

    render() {

        if (this.props.characters === null | this.props.loading) {
            return;
        }
        return (
            <div>
                <div>
                    <ScenesResults
                        computed_score={this.props.computed_score}
                        characters={this.props.characters}
                        message_result={this.props.message_result}
                        scenes={this.props.scenes}
                        file={this.props.file} />
                </div>
                <div>
                    <CharacterList
                        characters={this.props.characters}
                        handleSubmit={this.props.handleSubmit}
                        handleChange={this.props.handleChange}
                        file={this.props.file} />
                </div>
            </div>
        );
    }
}

export default Results;