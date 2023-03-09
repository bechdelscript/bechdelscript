import { Component } from "react";
import Character from "./character";
import Box from '@mui/material/Box';


class CharacterList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            characters: props.characters
        };
    }

    render() {
        const rows = [];
        for (let i = 0; i < this.state.characters.length; i++) {
            rows.push(
                <Character
                    name={this.state.characters[i].name}
                    gender={this.state.characters[i].gender}
                />
            );
        }
        return (
            <Box sx={{ minWidth: 120, maxHeight: 30 }}>
                <div className="characters-list">
                    <h1>List of characters</h1>
                    <ul>{rows}</ul>
                </div>
            </Box>
        )
    }
}

export default CharacterList;