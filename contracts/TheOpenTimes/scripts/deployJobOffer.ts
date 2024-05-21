import dotenv from 'dotenv'; 
dotenv.config()
import { Address, SendMode, SenderArguments, beginCell, contractAddress, fromNano, internal, loadCommonMessageInfo, storeCommonMessageInfo, storeMessageRelaxed, toNano } from '@ton/core';
import { JobOffer, storeRevoke } from '../wrappers/JobOffer';
import { NetworkProvider } from '@ton/blueprint';
import { storeDeploy, storeTransfer } from '../wrappers/JobOffer';
import { buildOnchainMetadata } from "../utils/jetton-helpers";
import { TokenMaster } from '../wrappers/TokenMaster';
import { mnemonicToPrivateKey } from 'ton-crypto';
import { TonClient, TonClient4, WalletContractV4 } from '@ton/ton';
import { randomUUID } from 'crypto';
import { log } from 'console';
import { content } from './deployMaster';

const jetton_master_deployer = process.env.DEPLOYER_MNEMONIC || "";
const jetton_master_deployer_mnem = jetton_master_deployer?.split(" ");
const poster_mnemonic_str = process.env.POSTER_MNEMONIC || "";
const poster_mnemonic = poster_mnemonic_str?.split(" ");

const title = "Sell Bike 2"
const description = "Selling a bike in excellent condition! Trek brand, 2022 model. Lightweight aluminum frame, disc brakes, 21 speeds. Ideal for city trips and long walks. Includes: headlights, bell, running board. Price 25,000 rub. Negotiable. Call: +7-999-123-45-67." 
const price = toNano(100)
const order = "Sell Bike 2"
const deployAmount = toNano("0.65")

export async function run(provider: NetworkProvider) {
    // let client = provider
    let client = new TonClient4({ endpoint: 'https://testnet-v4.tonhubapi.com' })
    let workchain = 0;

    let keyPairDeployer = await mnemonicToPrivateKey(jetton_master_deployer_mnem);
    let secretKeyDeployer = keyPairDeployer.secretKey;
    let deployer_wallet = WalletContractV4.create({
        workchain,
        publicKey: keyPairDeployer.publicKey,
    });
    let deployer_wallet_contract = client.open(deployer_wallet);
    const master = client.open(await TokenMaster.fromInit(
        deployer_wallet.address, content
    ));


    let keyPairPoster = await mnemonicToPrivateKey(poster_mnemonic);
    let secretKeyPoster = keyPairPoster.secretKey;
    let poster_wallet = WalletContractV4.create({
        workchain,
        publicKey: keyPairPoster.publicKey,
    });
    let poster_wallet_contract = client.open(poster_wallet);
    let sss = poster_wallet_contract.sender(keyPairPoster.secretKey)

    let JOInit = await JobOffer.init(
        title, description, price, order, master.address
    )    
    let JOInitAddress = contractAddress(workchain, JOInit);

    let deploy_msg = beginCell().endCell();
    let seqno: number = await poster_wallet_contract.getSeqno();
    let balance: bigint = await poster_wallet_contract.getBalance();
    console.log("Current deployment wallet balance = ", fromNano(balance).toString(), "💎TON");
    console.log("Deployer address = ", poster_wallet_contract.address);
    log("Job offer address: ", JOInitAddress)
    
    // await poster_wallet_contract.sendTransfer({
    //     seqno,
    //     secretKey: secretKeyPoster,
    //     messages: [
    //         internal({
    //             to: JOInitAddress,
    //             value: deployAmount,
    //             bounce: false,
    //             init: {
    //                 code: JOInit.code,
    //                 data: JOInit.data,
    //             },
    //             body: deploy_msg,
    //         }),
    //     ],
    // });
    // let destination_address = Address.parse("kQC1y6T5KWWXJli-QdxReuC4ENl2TLb7ZGPzWZDxojGAe-90")
    // let transferMessagePkg = beginCell().store(
    //     storeTransfer({
    //         $$type: "Transfer",
    //         query_id: 1n,
    //         amount: 1000n,
    //         destination: destination_address,
    //         response_destination: deployer_wallet_contract.address,
    //         custom_payload: beginCell().endCell(),
    //         forward_ton_amount: toNano(0.4),
    //         forward_payload: beginCell().endCell(),
    //     })
    //     )
    //     .endCell()
    // seqno = await deployer_wallet_contract.getSeqno()
    // await deployer_wallet_contract.sendTransfer({
    //     seqno,
    //     secretKey: secretKeyDeployer,
    //     messages: [internal({
    //         to: master.address,
    //         value: "0.1",
    //         body: transferMessagePkg,
    //     })],
    // });


    // seqno = await poster_wallet_contract.getSeqno();
    // balance = await poster_wallet_contract.getBalance();
    // let msg_revoke = beginCell().store(
    //     storeRevoke({
    //         $$type: "Revoke",
    //         query_id: 1n,
    //     })
    // ).endCell()
    // await poster_wallet_contract.sendTransfer({
    //     seqno,
    //     secretKey: secretKeyPoster,
    //     messages: 
    //         [internal({
    //             to: JOInitAddress,
    //             value: "0.1",
    //             body: "restart",
    //             // bounce: false
    //         })
    //     ]
    // })
    
}
