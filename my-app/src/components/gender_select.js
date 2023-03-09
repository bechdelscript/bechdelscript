import * as React from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

export default function GenderSelect(props) {

    return (
        <Box sx={{ minWidth: 120 }}>
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
        </Box>
    );
}