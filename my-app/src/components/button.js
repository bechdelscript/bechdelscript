import { Component } from "react";
import Button from '@mui/material/Button';

class UploadButton extends Component {
    constructor(props) {
        super(props);
        // this.onSubmit = this.onSubmit.bind(this);
        this.state = {
            onSubmit: null,
        }
    }

    handleSubmit(e) {
        // e.preventDefault()
        // console.log(Object.getPrototypeOf(Object.getPrototypeOf(Object.getPrototypeOf(e.target.files[0]))).valueOf())
        this.setState({
            onSubmit: e.target.files[0].name
            // onSubmit: e.target.files[0].prototype //.Blob.Object.FiletoString()
        })
    }

    render() {
        const status = this.state.onSubmit;
        console.log("status" + status)
        return (
            <div>
                <div>{status}</div>
                <Button variant="contained" component="label">
                    Upload
                    <input hidden accept=".txt" multiple={false} type="file"
                        onChange={(file) => this.handleSubmit(file)}
                    // onChange={() => console.log('click')}
                    />
                </Button>
            </div>
        );

    }
}

export default UploadButton;