import http from 'k6/http';
import exec from 'k6/execution';
import { check } from 'k6';

export const options = {
    vus: 30,
    duration: "10s",
};

export default function () {
    const vu_id = exec.vu.idInTest;

    const path = "/account/syncData";
    const payload = JSON.stringify(
        {},
    );
    const params = {
        headers: {
            "secret": `k6_${vu_id}`,
        },
    };

    const url = `http://127.0.0.1:8443${path}`;

    const res = http.post(url, payload, params);

    check(res, { "status code is 200": (r) => r.status === 200, });
}