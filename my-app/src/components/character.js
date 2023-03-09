import { Component } from "react";
import GenderSelect from "./gender_select";

class Character extends Component {

    render() {
        return (
            <li className="character">
                <h2>{this.props.name}</h2>
                <h2>{this.props.gender}</h2>
                <GenderSelect gender={this.props.gender} handleChange={this.props.handleChange} />
            </li>
        )
    }
}

export default Character;