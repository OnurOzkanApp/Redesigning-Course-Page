/* variables*/
let userLoc = document.getElementsByClassName('userinteraction')[0];


/* functions*/
function hoverLink(x) {
    x.style.color = 'grey';
    x.style.textDecoration = 'underline';
    x.style.backgroundColor = 'white';
    x.style.backgroundSize = '5%';
    x.style.transition = '500ms ease';
}

// link effects
function clickLink(x) {
    x.style.color = 'red';
    x.style.textDecoration = 'underline';
    x.style.transition = '100ms ease';
}
function changeBackLink(x) {
    x.style.color = '';
    x.style.textDecoration = '';
    x.style.backgroundColor = '';
    x.style.transition = '800ms ease';
}

function dropdownMenu() {
    /* variables*/
    let menu = document.getElementById('dropdownmenu');
    let arrow = document.getElementById('arrow');

    /* check if the drop down menu is closed*/
    if (menu.style.width == '') {
        menu.style.visibility = 'visible';
        menu.style.width = '12vw';
        arrow.style.transform = 'rotate(180deg)';
    } else {
        menu.style.width = '';
        menu.style.visibility = 'hidden';
        arrow.style.transform = '';
    }
    menu.style.transition = '500ms cubic';
    arrow.style.transition = '500ms ease';
}


