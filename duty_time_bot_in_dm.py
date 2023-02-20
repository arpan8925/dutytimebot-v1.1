import discord
import json
import http.client
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content == '!duty':
        await message.channel.send('Please enter your On duty and Off duty time in the format: HH:MM - HH:MM')

    if message.content.startswith('!duty '):
        # Extract on duty and off duty times from message
        times = message.content.split(' ')[1].split('-')
        if len(times) != 2:
            await message.channel.send('Invalid time range format. Please try again.')
            return
        on_duty = times[0].strip().replace('.', ':').replace('m', '').replace('M', '').replace(' ', '')
        off_duty = times[1].strip().replace('.', ':').replace('m', '').replace('M', '').replace(' ', '')
        
        # Get the user who sent the message
        user = message.author.name
        
        # Send a response back to the user
        response = f"Thanks, {user}, for providing your duty times. Your on duty time is {on_duty} and your off duty time is {off_duty}."
        await message.channel.send(response)

        # Construct the payload in the json format
        payload = json.dumps({"action": "store_duty_time", "on_duty": on_duty, "off_duty": off_duty, "user": user})
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPSConnection('dollerpayfast.xyz')
        conn.request('POST', '/wp-admin/admin-ajax.php', payload, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        print(f'HTTP response: {res.status} {res.reason}')
        print(f'Response data: {data}')
        
        # Create a new WordPress post with the duty times
        wp = Client('https://dollerpayfast.xyz/xmlrpc.php', 'sbxp1966@gmail.com', 'sbxp1966@gmail.comsbxp1966@gmail.com')
        post = WordPressPost()
        post.title = 'Duty Time'
        post.post_type = 'duty'
        post.custom_fields = [{'key': 'on_duty', 'value': on_duty}, {'key': 'off_duty', 'value': off_duty}, {'key': 'user', 'value': user}]
        post.id = wp.call(NewPost(post))
        print(f'New WordPress post created with ID {post.id}')
        
        # Send a confirmation message to the Discord user
        await message.channel.send(f'Your on duty time is {on_duty} and off duty time is {off_duty}. This has been recorded in WordPress.')

client.run('BOT TOKEN HERE')
