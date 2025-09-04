/* variables*/
let remarkBackground = document.getElementsByClassName('remarkbackground')[0];
let remarkContent = document.getElementsByClassName('remarkcontent')[0];
let studentBody = document.body;

/* functions*/
function openRemarkWindow() {
    remarkBackground.style.visibility = 'visible';
    remarkContent.style.visibility = 'visible';
    studentBody.style.overflowY = 'hidden';
}

function closeWindow() {
    remarkBackground.style.visibility = 'hidden';
    remarkContent.style.visibility = 'hidden';
    studentBody.style.overflowY = '';
}
