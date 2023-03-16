import React, { Component } from "react";
import Character from "./character";
import Button from '@mui/material/Button';


class CharacterList extends Component {

    render() {
        const rows = [];
        for (let i = 0; i < this.props.characters.length; i++) {
            rows.push(
                <Character
                    key={this.props.characters[i].name + toString(i)}
                    name={this.props.characters[i].name}
                    gender={this.props.characters[i].gender}
                    handleChange={(e) => this.props.handleChange(i, e)}
                />
            );
        }
        return (
            <form onSubmit={this.props.handleSubmit}>
                <div className="characters-area-container">
                    <h2>List of characters</h2>
                    <div>{rows}</div>
                </div>
                <Button type="submit">Test again !</Button>
            </form>
        )
    }
}

export default CharacterList;