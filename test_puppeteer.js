
const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));
    await page.goto('file:///' + 'c:/Users/You/OneDrive/Desktop/Bhai & MID/TutorBhaiya/courses.html'.replace(/ /g, '%20'));
    
    // Check if bKash modal exists
    const bkashModal = await page.\\#bkash-modal;
    console.log('bKash Modal exists:', !!bkashModal);
    
    await browser.close();
})();

