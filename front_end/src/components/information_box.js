import * as React from 'react';
import Grid from '@mui/material/Grid';
import { Link } from '@mui/material';

import { ReactComponent as WelcomeText } from './images/welcome_text.svg';
import { ReactComponent as TestIllustration } from './images/test_explanation.svg';



export default function InformationBox(props) {

    if (!(props.characters === null)) {
        return;
    }

    return (
        <>

            <Grid container item xs={12} className="information-box-container padding-40px-horizontal-20px-vertical" rowSpacing={2} columnSpacing={0.1}>
                <WelcomeText className="padding-20px width-70percent center-text" />

                <Grid item xs={6} >
                    <div className='bubble info-bubble-general max-height-fit-content'>
                        <div className="padding-40px">
                            This tool was made to facilitate the process of assessing if a movie passes the <b>Bechdel-Wallace Test</b> or not. If you don't know what the Bechdel test is, check out <Link href="https://bechdeltest.com" underline="hover">this site</Link> !
                            <br /><br />Our tool is not perfect in any way, but it is useful, and was made to be accessible and useful.
                            <br /><br />The tool is also fully <b>open source</b>. You can explore our code <Link href="https://github.com/bechdelscript" underline="hover">here</Link>.
                        </div>
                    </div>
                </Grid>
                <Grid item xs={6}>
                    <TestIllustration className="padding-40px-horizontal-20px-vertical max-height-200px" />
                </Grid>
                <Grid container item xs={6} rowSpacing={2} >
                    <div className='bubble info-bubble-upload max-height-fit-content'>
                        <div className='padding-20px'>
                            <i><b>Uploading a File</b></i><br /><br />
                            <div className='left-align-text'>
                                You can upload a movie script to test it using a .txt format file. Lots of scripts can easily be found online, if you don't know where to look we recommend the <Link href='https://imsdb.com/' underline="hover"> IMSDB website</Link>.
                            </div>
                        </div>
                    </div>
                    <div className='bubble info-bubble-results max-height-fit-content'>
                        <div className='padding-40px-horizontal-20px-vertical'>
                            <i><b>Understanding the Score and Results</b></i><br /><br />
                            <div className="left-align-text">
                                When uploading a script, you will get access to a Bechdel score prediction, along with the score justification.
                                <ul className="padding-20px-horizontal">
                                    <li>If the predicted score is 0 or 1, you will only have access to the list of identified characters and their predicted gender.</li>
                                    <li>If the predicted score is 2, you will have access to the character list, aswell as to dialogues including women characters. The man-related sentences will be hightlighted in orange.</li>
                                    <li>If the predicted score is 3, you will have access to the character list and to the scenes that validate the test. The lines said by women that are not man-related will be highlighted in yellow.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </Grid>
                <Grid item xs={6}>
                    <div className='bubble info-bubble-parameters  max-height-fit-content'>
                        <div className="padding-40px-horizontal-20px-vertical">
                            <i><b>Choosing the parameters</b></i><br /><br />
                            <div className="left-align-text">
                                The Parameters options in the upper right hand corner correspond to how strict you want to be in the Bechdel test criteria.
                                Does the conversation have to only include women ?
                                Does the entire conversation have to be about something else than a man ? You have three possible options :
                                <ul className="padding-20px-horizontal">
                                    <li>By putting both parameters to True, a movie will only pass the test if there's a conversation only women speak in that never mentions a man. This is the strictest option.</li>
                                    <li>By putting Only women in the scene to True and Whole discussion not about men to False, a movie will pass the test if there is a conversation in the movie where only women and present, but they are allowed to mention a man at some point, as long as they exchange a few lines about something else.</li>
                                    <li>By putting both parameters to False, a movie will pass the test even if a man is included in a conversation where at least two women exchange a few consecutive lines about something other than a man.</li>
                                    <li>The last option (Only women in the scene as False and Whole discussion not about men as True) is forbidden : we consider that it's impossible for a man to be in a conversation and for the conversation to not mention men.</li>
                                </ul>
                            </div>
                        </div>
                    </div><br />
                </Grid>
                <Grid xs={6}>
                    <div className='bubble info-bubble-characters max-height-fit-content'>
                        <div className="padding-40px-horizontal-20px-vertical">
                            <i><b>Exploring the characters</b></i><br /><br />
                            <div className='left-align-text'>
                                The character list with their predicted genders (F, M, NB) is a way for you to identify potential errors. If you believe a character has been wrongly gendered,
                                correct it and re-test the script. This way, you'll get a more accurate score and validating scenes thanks to your insight.
                            </div>
                        </div>
                    </div>
                </Grid>
                <Grid xs={6}>
                    <div className='bubble info-bubble-disclaimer max-height-fit-content'>
                        <div className="padding-40px-horizontal-20px-vertical">
                            <i><b>Disclaimer</b></i><br /><br />
                            <div className='left-align-text'>
                                Please note that, in order to promote inclusivity, the module can gender a character as a Woman, a Man or a Non-Binary individual. However, we have not implemented Bechdel rules that allow a conversation between two gender minorities (a woman and a non-binary person, for instance) to validate the second criteria. That is because we felt it was out of our scope to swerve away from the original test that much. However, we feel that as Non-binary folk representation in movies is increasing, it would be ideal to update the test rules and implement our module accordingly.
                            </div>
                        </div>
                    </div>
                </Grid>
            </Grid>
        </>
    );
}
