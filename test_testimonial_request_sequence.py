import unittest
from unittest.mock import MagicMock, patch

import testimonial_request_sequence as sequence


class TestTestimonialRequestSequence(unittest.TestCase):
    def test_email_has_reply_path_and_prefilled_form(self):
        message = sequence.build_email("<script> Alex", "alex+jobs@example.com")

        self.assertIn("reply directly", message["text"])
        self.assertIn("email=alex%2Bjobs%40example.com", message["text"])
        self.assertIn("&lt;script&gt;", message["html"])
        self.assertNotIn("<script>", message["html"])

    @patch.dict("os.environ", {"RESEND_API_KEY": "test-key"})
    @patch.object(sequence.requests, "post")
    def test_send_uses_stable_idempotency_key(self, post):
        post.return_value.json.return_value = {"id": "resend-id"}

        sequence.send_request(42, "alex@example.com", "Alex")

        self.assertEqual(post.call_args.kwargs["headers"]["Idempotency-Key"], "testimonial-request/42")
        self.assertEqual(post.call_args.kwargs["json"]["to"], "alex@example.com")

    def test_eligible_query_uses_paid_plan_age_and_sent_marker(self):
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value.fetchall.return_value = []

        sequence.get_eligible_users(conn)

        query, params = conn.cursor.return_value.__enter__.return_value.execute.call_args.args
        self.assertIn("LOWER(u.plan) <> 'free'", query)
        self.assertIn("u.testimonial_request_sent_at IS NULL", query)
        self.assertIn("INTERVAL '7 days'", query)
        self.assertIn("NOT EXISTS", query)
        self.assertEqual(params, (100,))


if __name__ == "__main__":
    unittest.main()
