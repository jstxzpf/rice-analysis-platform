import { createRouter, createWebHistory } from 'vue-router';
import Layout from '../layout/Layout.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import FieldManagement from '../views/FieldManagement.vue';
import DataUpload from '../views/DataUpload.vue';
import FieldDetail from '../views/FieldDetail.vue';
import AnalysisReport from '../views/AnalysisReport.vue';
import Dashboard from '../views/Dashboard.vue';
import TrendAnalysis from '../views/TrendAnalysis.vue';
import VisualAnalysis from '../views/VisualAnalysis.vue';
import InterFieldComparison from '../views/InterFieldComparison.vue';
import IntraFieldComparison from '../views/IntraFieldComparison.vue';

const routes = [
    {
        path: '/',
        component: Layout,
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: Dashboard,
            },
            {
                path: 'fields',
                name: 'FieldManagement',
                component: FieldManagement,
            },
            {
                path: 'fields/:id',
                name: 'FieldDetail',
                component: FieldDetail,
                props: true,
            },
            {
                path: 'fields/:id/trends',
                name: 'TrendAnalysis',
                component: TrendAnalysis,
                props: true,
            },
            {
                path: 'upload',
                name: 'DataUpload',
                component: DataUpload,
            },
            {
                path: 'results/:id',
                name: 'AnalysisReport',
                component: AnalysisReport,
                props: true,
            },
            {
                path: 'visual-analysis',
                component: {
                    template: '<router-view />',
                },
                redirect: '/visual-analysis/home',
                children: [
                    {
                        path: 'home',
                        name: 'VisualAnalysis',
                        component: VisualAnalysis,
                    },
                    {
                        path: 'inter-field',
                        name: 'InterFieldComparison',
                        component: InterFieldComparison,
                    },
                    {
                        path: 'intra-field',
                        name: 'IntraFieldComparison',
                        component: IntraFieldComparison,
                    },
                ]
            },
            // Other authenticated routes will go here as children
        ]
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
    const publicPages = ['Login', 'Register'];
    const authRequired = !publicPages.includes(to.name as string);
    const token = localStorage.getItem('access_token');

    if (authRequired && !token) {
        return next('/login');
    }

    next();
});

export default router;
