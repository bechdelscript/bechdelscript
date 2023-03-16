import React, { Component } from "react";
import { Switch, Typography } from "@mui/material";
import FormControlLabel from '@mui/material/FormControlLabel';
import FormGroup from '@mui/material/FormGroup';


class Parameters extends Component {

    render() {
        return (
            <div className="parameters-area-container">
                <Typography variant="h4">Parameters</Typography>
                <FormGroup>
                    <FormControlLabel
                        control={<Switch
                            onChange={this.props.handleWomenSwitch}
                            checked={this.props.checkedWomenSwitch}
                        />}
                        label={<Typography variant="body1">Only women in scene</Typography>}
                    />
                    <FormControlLabel
                        control={<Switch
                            onChange={this.props.handleDiscussionSwitch}
                            checked={this.props.checkedDiscussionSwitch}
                        />}
                        label={<Typography variant="body1">Whole discussion not about men</Typography>}
                    />
                </FormGroup>
            </div>
        );
    }
}

export default Parameters;