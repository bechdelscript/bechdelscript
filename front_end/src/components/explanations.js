import { Component } from "react";
import { Typography } from "@mui/material";


class Explanation extends Component {

    render() {
        return (
            <>
                <div className="explanation-area-container">
                    <Typography variant="h4">The Bechdel-Wallace Test</Typography>
                    <div className="left-align-text">
                        A movie passes the Bechdel test if :<ol>
                            <li>There are two named female characters</li>
                            <li>They talk with each other</li>
                            <li>About something other than a man</li>
                        </ol>
                    </div>
                </div>
            </>
        );
    }
}

export default Explanation;