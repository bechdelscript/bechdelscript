import * as React from 'react';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Grid from '@mui/system/Unstable_Grid/Grid';

export default function GenderSelect(props) {

    return (
        <Grid item xs={5}>
            <FormControl fullWidth>
                <InputLabel id="demo-simple-select-label">Gender</InputLabel>
                <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={props.gender}
                    label="Gender"
                    onChange={props.handleChange}
                >
                    <MenuItem value={'m'}>Male</MenuItem>
                    <MenuItem value={'f'}>Female</MenuItem>
                    <MenuItem value={'nb'}>Non Binary</MenuItem>
                </Select>
            </FormControl>
        </Grid>
    );
}