import React, { useState } from 'react';
import { Button } from '@mui/material';

function FileUpload(props) {
    return (
        <form onSubmit={props.handleSubmit}>
            <input type="file" onChange={props.handleFileSelect} />
            <Button type="submit">Upload</Button>
        </form>
    );
}

export default FileUpload;