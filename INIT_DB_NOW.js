// COPY AND PASTE THIS INTO YOUR BROWSER CONSOLE (F12) RIGHT NOW!

(async function() {
    console.log('🚀 Initializing database...');
    try {
        const response = await fetch('https://beauty-aryan-back-production.up.railway.app/api/v1/init-database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        console.log('✅ Response:', data);
        if (data.status === 'success') {
            console.log('✅ Database initialized successfully!');
            console.log('🔄 Refreshing page in 2 seconds...');
            setTimeout(() => window.location.reload(), 2000);
        } else {
            console.error('❌ Error:', data);
        }
    } catch (error) {
        console.error('❌ Error:', error);
    }
})();

