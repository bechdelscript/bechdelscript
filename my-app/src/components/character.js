import { Component } from "react";
import GenderSelect from "./gender_select";

class Character extends Component {
    constructor(props) {
        super(props);
        this.state = {
            name: props.name,
            gender: props.gender
        };
    }

    render() {
        return (
            <li className="character">
                <h2>{this.state.name}</h2>
                <h2>{this.state.gender}</h2>
                <GenderSelect gender={this.state.gender} />
            </li>
        )
    }
}

export default Character;