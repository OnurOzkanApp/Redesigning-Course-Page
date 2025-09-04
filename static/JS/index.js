/* variables*/
let overlay = document.getElementsByClassName('gradient-overlay');
let header = document.getElementById('headercontbackground');
let blueLogo = document.getElementById('uoftbluetoplogo');
let whiteLogo = document.getElementById('uoftwhitetoplogo');
let firstSec = document.getElementById('coursedescription');
let leftTable = document.getElementById('lefttable');
let rightTable = document.getElementById('righttable');
let iframe = document.getElementsByTagName('iframe')[0];

/* user scrolling for header and page animations */
window.addEventListener('scroll', function () {
    // makes header visible
    if (window.scrollY > 120) {
        header.style.backgroundColor = 'black';
        header.style.transition = '300ms ease';
        blueLogo.style.visibility = 'hidden';
        blueLogo.style.width = '0';
        whiteLogo.style.visibility = 'visible';

        // makes page tables change colour
        if (window.scrollY > 200) {
            leftTable.style.backgroundColor = '#25355A';
            leftTable.style.color = '#F2F4F7';
            leftTable.style.transition = '2500ms ease';
            rightTable.style.backgroundColor = '#25355A';
            rightTable.style.color = '#F2F4F7';
            rightTable.style.transition = '2500ms ease';

            // calendar animation
            if (window.scrollY > 1200) {
                iframe.style.visibility = 'visible';
                iframe.style.width = '100%';
                iframe.style.transition = '3000ms ease';

            }
        }
        // reverts header
    } else if (window.scrollY <= 120){
        header.style.backgroundColor = '';
        header.style.transition = '700ms ease';
        blueLogo.style.visibility = 'visible';
        blueLogo.style.width = '';
        whiteLogo.style.visibility = 'hidden';

    }
})

// header background image effects
function focusPic() {
    overlay[0].style.filter = 'blur(0)';
    overlay[0].style.transition = '500ms ease';
}
function blurPic() {
    overlay[0].style.filter = 'blur(0.75px)';
    overlay[0].style.transition = '500ms ease';

}

// animation on page load
function animatedTables() {
    firstSec.style.backgroundColor = '#25355A';
    firstSec.style.color = '#F2F4F7';
    firstSec.style.transition = '500ms ease';
}