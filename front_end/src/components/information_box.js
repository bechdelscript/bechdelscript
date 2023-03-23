import * as React from 'react';


export default function InformationBox() {

    return (
        <>
            <div className="information-box-container">
                <b>Welcome to the Bechdel Script Tester !</b>
                <div className="left-align-text">
                    A movie passes the Bechdel test if :
                    <ol>
                        <li>There are two named female characters</li>
                        <li>They talk with each other</li>
                        <li>About something other than a man</li>
                    </ol>
                </div>
            </div>
        </>
    );
}