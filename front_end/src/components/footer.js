import React from 'react';
import { Grid } from '@mui/material';
import { Link } from '@mui/material';
import logo_centralesupelec from './images/logo-centralesupelec.png';
import logo_illuin from './images/logo-illuin-technology.png';


export default function Footer(props) {
    return (
        <Grid container>
            <Grid item xs></Grid>
            <Grid item container alignItems="center" justifyContent="center" xs={3}>
                <img src={logo_illuin} height={50}></img>
            </Grid>
            <Grid item container alignItems="center" justifyContent="center" xs={3}>
                <img src={logo_centralesupelec} height={50}></img>
            </Grid>
            <Grid item xs={3} container alignItems="center" justifyContent="center">
                <span className="text-link-pink"><Link href="mailto:bechdelscript@gmail.com" underline="hover" color="inherit"> Send us an email</Link></span>
            </Grid>
            <Grid item xs></Grid>
        </Grid >
    );
}