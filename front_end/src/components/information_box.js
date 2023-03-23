import * as React from 'react';


export default function InformationBox() {

    return (
        <>
            <b>TO DO : reduce spaces above and below container. Pimp the look inside container.</b>
            <div className="information-box-container">
                <b>Welcome to the Bechdel Script Tester !</b> <br />
                TO DO : phrase d'intro. Automated tester. Not really perfect, at all levels. Tool openly available to everyone, transparency. Github : TO DO LINK.
                <div className="left-align-text">
                    Upload Section<br />
                    TO DO : Describe the format of a script
                </div>
                <div className="left-align-text">
                    Parameters Section<br />
                    TO DO : What do they mean ? Describe the 3 possible configurations.
                </div>
                <div className="left-align-text">
                    Score and Result Section <br />
                    See the score out of the three criteria, and if possible, see the scenes (and highlighted dialogues) that validate the score.
                </div>
                <div className="left-align-text">
                    Characters Section<br />
                    Allow you to see which characters are identified by our parser, and how they were gendered. In case of an error, you can modify a character's gender and test the script again with the updated genders.
                </div>
            </div>
        </>
    );
}