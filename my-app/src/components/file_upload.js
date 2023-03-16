import React from "react";
import { Typography, Grid, Button, Box } from '@mui/material';
import { CircularProgress } from '@mui/material';


function FileUpload(props) {
    let loading = props.loading ? <CircularProgress className="spinner" /> : null;
    let chosen_file = props.file ? props.file.name : `No file chosen`
    return (
        <div className="uploader-area-container">
            <Typography variant="h4">Upload a file</Typography>
            <form onSubmit={props.handleSubmit}>
                <Grid container>
                    <Grid item xs={12}>
                        <Box sx={{ justifyContent: 'center', flexWrap: 'nowrap' }}>
                            <Button sx={{ m: 0.5 }} component="label">
                                Choose file
                                <input hidden type="file" onChange={props.handleFileSelect} />
                            </Button>
                            {chosen_file}
                        </Box>
                    </Grid>
                    <Grid item xs={12}>
                        <Button sx={{ m: 1 }} variant="contained" type="submit">Upload</Button>
                    </Grid>
                </Grid>
            </form>
            <div>{props.loading ? '' : props.error_message}</div>
            <div>{loading}</div>
        </div >
    );
}

export default FileUpload;