import { Component } from "react";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Grid from '@mui/material/Grid';
import { Box } from "@mui/system";


const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        },
    },
};

class SceneDisplayer extends Component {

    constructor(props) {
        super(props);
        this.state = {
            value: this.props.scenes[0],
            text: " INSIDE THE TENT LUKE's eyes pop open, disoriented, realizing he's fallen asleep reading by flashlight. He's nineteen, still slightly awkward and unaware he's growing handsome. He listens as the ENGINE RUMBLES LOUDER, closer. He peers out through the tent flap. Glaring head lamps ROAR toward him. Scrambling out of his sleeping bag, he HURLS himself against the side of the tent, as... AAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit. Ut velit mauris, egestas sed, gravida nec, ornare ut, mi. Aenean ut orci vel massa suscipit pulvinar. Nulla sollicitudin. Fusce varius, ligula non tempus aliquam, nunc turpis ullamcorper nibh, in tempus sapien eros vitae ligula. Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur aliquet pellentesque diam. Integer quis metus vitae elit lobortis egestas. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi vel erat non mauris convallis vehicula. Nulla et sapien. Integer tortor tellus, aliquam faucibus, convallis id, congue eu, quam. Mauris ullamcorper felis vitae erat. Proin feugiat, augue non elementum posuere, metus purus iaculis lectus, et tristique ligula justo vitae magna. Aliquam convallis sollicitudin purus. Praesent aliquam, enim at fermentum mollis, ligula massa adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce vulputate sem at sapien. Vivamus leo. Aliquam euismod libero eu enim. Nulla nec felis sed leo placerat imperdiet. Aenean suscipit nulla in justo. Suspendisse cursus rutrum augue. Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel rhoncus faucibus, felis magna fermentum augue, et ultricies lacus lorem varius purus. Curabitur eu amet",
        };
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
    }

    render() {
        const rows = [];
        for (let i = 0; i < this.props.scenes.length; i++) {
            rows.push(
                <MenuItem value={this.props.scenes[i]} key={"Scene number " + i.toString()}>
                    {"Scene number " + this.props.scenes[i].toString()}
                </MenuItem>
            );
        }
        return (
            <div>
                <Grid container spacing={5} columns={12}>
                    <Grid item style={{ margin: 'auto' }} xs={6}>
                        Choose a scene :
                    </Grid>
                    <Grid item xs={6}>
                        <InputLabel id="simple-scene-select-label" ></InputLabel>
                        <Select
                            style={{ width: '100%' }}
                            labelId="simple-scene-select-label"
                            id="simple-scene-select"
                            value={this.state.value}
                            onChange={(e) => this.handleChange(e)}
                            MenuProps={MenuProps}
                        >
                            {rows}
                        </Select>
                    </Grid>
                </Grid>
                <br />
                <Box style={{ maxHeight: 250, overflow: 'auto', background: '#ffffff' }}>
                    <div style={{ padding: '2%', textAlign: 'left' }} >{this.state.text}</div>
                </Box>
            </div>
        );
    }

}

export default SceneDisplayer;
