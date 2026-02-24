import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import './Layout.css';

export default function Layout() {
    const { logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const menuItems = [
        { label: 'Dashboard', path: '/' },
        { label: 'Orders', path: '/orders' },
        { label: 'Clients', path: '/clients' },
        { label: 'Settings', path: '/settings' },
    ];

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <h2>SaaS Shopper</h2>
                </div>
                <nav className="sidebar-nav">
                    {menuItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                        >
                            {item.label}
                        </Link>
                    ))}
                </nav>
                <div className="sidebar-footer">
                    <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
                        Logout
                    </button>
                </div>
            </aside>
            <main className="main-content">
                <header className="topbar">
                    <div className="breadcrumbs">
                        {menuItems.find(m => m.path === location.pathname)?.label || 'Page'}
                    </div>
                </header>
                <div className="page-content">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
