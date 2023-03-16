import { Component } from "react";


class Explanation extends Component {

    render() {
        return (
            <>
                <div className="explanation-area-container">
                    <b>Welcome to the Bechdel Script Tester !</b>
                    <p className="left-align-text">
                        A movie passes the Bechdel test if :
                        <ol>
                            <li>There are two named female characters</li>
                            <li>They talk with each other</li>
                            <li>About something other than a man</li>
                        </ol>
                    </p>
                </div>
            </>
        );
    }
}

export default Explanation;