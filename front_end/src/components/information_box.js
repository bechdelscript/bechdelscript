import * as React from 'react';
import Grid from '@mui/material/Grid';


export default function InformationBox(props) {

    if (!(props.characters === null)) {
        return;
    }

    return (
        <>
            <Grid item xs={12}>
                <b>TO DO : reduce spaces above and below container. Pimp the look inside container : change font, width, and background color!</b>
                <div className="information-box-container">
                    <b>Welcome to the Bechdel Script Tester !</b><br /><br />
                    This tool was made to facilitate the process of assessing if a movie passes the Bechdel-Wallace Test or not. If you don't know what the Bechdel test is, check <a href="https://bechdeltest.com">this</a> out !
                    It is not perfect in any way, but it is useful, and was made to be used and accessible.
                    This tool is also fully open source. You can check out our code <a href="https://github.com/bechdelscript">here</a>. <br /><br />
                    <div>
                        <i><b>Uploading a File</b></i><br /><br />
                        You can upload a movie script to test it using a txt format file. They can easily be found online. The movie script does need to include parsing to differentiate dialogues from character names from narration, etc...
                    </div><br />
                    <div>
                        <i><b>Choosing the parameters</b></i><br /><br />
                        The Parameters options in the upper right hand corner correspond to how strict you want to be in the Bechdel test criteria.
                        Does the conversation have to only include women ?
                        Does the entire conversation have to be about something else than a man ? You have three possible options :
                        <li>By putting both parameters to True, a movie will only pass the test if there's a conversation only women speak in that never mentions a man. This is the strictest option.</li>
                        <li>By putting Only women in the scene to True and Whole discussion not about men to False, a movie will pass the test if there is a conversation in the movie where only women and present, but they are allowed to mention a man at some point, as long as they exchange a few lines about something else.</li>
                        <li>By putting both parameters to False, a movie will pass the test even if a man is included in a conversation where at least two women exchange a few consecutive lines about something other than a man.</li>
                        <li>The last option (Only women in the scene as False and Whole discussion not about men as True) is forbidden : we consider that it's impossible for a man to be in a conversation and for the conversation to not mention men.</li>
                    </div><br />
                    <div>
                        <i><b>Understanding the Score and Results</b></i><br /><br />
                        When uploading a script, you will get access to a Bechdel score prediction, along with the score justification.
                        <li>If the predicted score is 0 or 1, you will only have access to the list of identified characters and their predicted gender.</li>
                        <li>If the predicted score is 2, you will have access to the character list, aswell as to dialogues including women characters. The man-related sentences will be hightlighted in orange.</li>
                        <li>If the predicted score is 3, you will have access to the character list and to the scenes that validate the test. The lines said by women that are not man-related will be highlighted in yellow.</li>
                    </div><br />
                    <div>
                        <i><b>Exploring the characters</b></i><br /><br />
                        The character list with their predicted genders (F, M, NB) is a way for you to identify potential errors. If you believe a character has been wrongly gendered,
                        correct it and re-test the script. This way, you'll get a more accurate score and validating scenes thanks to your insight.
                    </div>
                    <div>
                        <i><b>Disclaimer</b></i><br /><br />
                        Please note that, in order to promote inclusivity, the module can gender a character as a Woman, a Man or a Non-Binary individual. However, we have not implemented Bechdel rules that allow a conversation between two gender minorities (a woman and a non-binary person, for instance) to validate the second criteria. That is because we felt it was out of our scope to swerve away from the original test that much. However, we feel that as Non-binary folk representation in movies is increasing, it would be ideal to update the test rules and implement our module accordingly.
                    </div>
                </div>
            </Grid>
        </>
    );
}
