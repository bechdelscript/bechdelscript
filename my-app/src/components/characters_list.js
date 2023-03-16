import React, { Component } from "react";
import Character from "./character";
import Button from '@mui/material/Button';
import Grid from "@mui/system/Unstable_Grid/Grid";
import { Typography } from "@mui/material";


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
                    <Typography variant="h4" sx={{ m: 2 }}>List of characters</Typography>
                    <Grid container rowGap={2}>{rows}</Grid>
                    <Button sx={{ m: 2 }} type="submit" variant="contained">Test again !</Button>
                </div>
            </form >
            // {/* <input type="file" onChange={props.handleFileSelect} /> */ }
        )
    }
}

export default CharacterList;