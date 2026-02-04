import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import PrimeVue from 'primevue/config';

// Theme and Icons
import 'primevue/resources/themes/vela-blue/theme.css'; // Dark Theme
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';

// Import PrimeVue Components
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import Panel from 'primevue/panel';
import Timeline from 'primevue/timeline';
import Terminal from 'primevue/terminal';
import InputText from 'primevue/inputtext';

const app = createApp(App);

// Use Pinia for state management
app.use(createPinia());

// Use PrimeVue
app.use(PrimeVue, { ripple: true });

// Register Components Globally

app.component('Toolbar', Toolbar);

app.component('Button', Button);

app.component('Splitter', Splitter);

app.component('SplitterPanel', SplitterPanel);

app.component('Panel', Panel);

app.component('Timeline', Timeline);

app.component('Terminal', Terminal);

app.component('InputText', InputText);



// Register Directives

import Tooltip from 'primevue/tooltip';

app.directive('tooltip', Tooltip);



app.mount('#app');
