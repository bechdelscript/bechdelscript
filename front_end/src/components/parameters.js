import React, { Component } from "react";
import { Switch, Typography } from "@mui/material";
import FormControlLabel from '@mui/material/FormControlLabel';
import FormGroup from '@mui/material/FormGroup';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const green_theme = createTheme({
    palette: {
        primary: {
            main: '#4a5a2c',
        },
    },
});


class Parameters extends Component {

    render() {
        return (
            <div className="parameters-area-container">
                <Typography variant="h4">Parameters</Typography>
                <FormGroup>
                    <FormControlLabel
                        control={
                            <ThemeProvider theme={green_theme}>
                                <Switch
                                    onChange={this.props.handleWomenSwitch}
                                    checked={this.props.checkedWomenSwitch}
                                />
                            </ThemeProvider>
                        }
                        label={<Typography variant="body1">Only women in scene</Typography>}
                    />
                    <FormControlLabel
                        control={
                            <ThemeProvider theme={green_theme}>
                                <Switch
                                    onChange={this.props.handleDiscussionSwitch}
                                    checked={this.props.checkedDiscussionSwitch}
                                />
                            </ThemeProvider>
                        }
                        label={<Typography variant="body1">Whole discussion not about men</Typography>}
                    />
                </FormGroup>
            </div>
        );
    }
}

export default Parameters;