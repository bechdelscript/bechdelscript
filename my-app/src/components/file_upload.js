import React, { useState } from 'react';
import { Button } from '@mui/material';

function FileUpload() {
    const [file, setFile] = useState(null);

    const handleFileSelect = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch("http://localhost:8000/upload_script/", {
            method: 'POST',
            body: formData,
        });
        console.log(response);
        const test = await response.json()
        console.log(test)
    };

    const receiveScript = async () => {
        console.log("receiveScript");
        const response = await fetch("http://localhost:8000/list-scripts/")
        console.log(response)
        const test = await response.json()
        console.log(test)

    }


    return (
        <form onSubmit={handleSubmit}>
            <input type="file" onChange={handleFileSelect} />
            <Button type="submit">Upload</Button>
            {/* <button type="submit">Upload</button> */}
        </form>
    );
}

export default FileUpload;