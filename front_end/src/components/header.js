import React from 'react';
import { Grid, Typography } from '@mui/material';
import logo_website from './images/logo-bechdelscript.svg';


export default function Header(props) {
    return (
        <Grid container>
            <Grid
                container
                direction="row"
                justifyContent="flex-end"
                alignItems="center"
                xs>
                <img src={logo_website} height={60}></img>
            </Grid>
            <Grid item xs={5}>
                <Typography variant='h3' className='padding-20px'>Bechdel Script Tester</Typography>
            </Grid>
            <Grid item xs>
            </Grid>

        </Grid >
    );
}