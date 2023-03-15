import React from "react";
import { Button } from '@mui/material';
import { CircularProgress } from '@mui/material';

function FileUpload(props) {
    let loading = props.loading ? <CircularProgress /> : null;
    let chosen_file = props.file ? props.file.name : `No file chosen`
    return (
        <div>
            <form onSubmit={props.handleSubmit}>
                <Button component="label">
                    Choose file
                    <input hidden type="file" onChange={props.handleFileSelect} />
                </Button>
                &nbsp;&nbsp;&nbsp;&nbsp;
                {chosen_file}
                <br></br>
                <Button variant="contained" type="submit">Upload</Button>
            </form>
            <div>{loading}</div>
        </div>
    );
}

export default FileUpload;