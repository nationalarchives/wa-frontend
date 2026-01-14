/**
 * Custom Header component with configurable mobile breakpoint.
 * TNA default is 48em (768px), we use 64em (1024px).
 */

const MOBILE_BREAKPOINT = '64em';

export default class Header {
    static selector() {
        return '[data-module="ukgwa-header"]';
    }

    constructor($module) {
        const button = $module.querySelector('.tna-header__navigation-button');
        const nav = $module.querySelector('.tna-header__navigation');

        if (!button || !nav) return;

        const mql = matchMedia(`(max-width: ${MOBILE_BREAKPOINT})`);
        let open = false;

        const sync = () => {
            const showNav = !mql.matches || open;

            nav.hidden = !showNav;
            nav.classList.toggle('tna-header__navigation--open', showNav);
            nav.setAttribute('aria-hidden', String(!showNav));

            button.classList.toggle(
                'tna-header__navigation-button--opened',
                open,
            );
            button.setAttribute('aria-expanded', String(open));
        };

        button.hidden = false;
        button.addEventListener('click', () => {
            open = !open;
            sync();
        });

        mql.addEventListener('change', () => {
            open = false;
            sync();
        });

        sync();
    }
}
