import React from 'react';
import { Grid } from '@mui/material';
import { Link } from '@mui/material';
import logo_centralesupelec from './images/logo-centralesupelec.png';
import logo_illuin from './images/logo-illuin-technology.png';


export default function Footer(props) {
    return (
        <Grid container>
            <Grid item xs={1}></Grid>
            <Grid item xs={3}>
                <img src={logo_illuin} height={50}></img>
            </Grid>
            <Grid item xs={3}>
                <img src={logo_centralesupelec} height={50}></img>
            </Grid>
            <Grid item xs={3}>
                <Link href="mailto:bechdelscript@gmail.com" underline="hover"> Send us an email</Link>
            </Grid>
            <Grid item xs={1}></Grid>
        </Grid >
    );
}